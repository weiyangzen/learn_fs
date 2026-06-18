# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_reqmanager.c

Purpose: converts high-level CPT VF crypto requests into DMA scatter/gather tables and hardware instructions, posts them to a VF command queue, and reaps completions from pending queues.

Important APIs and control flow: `process_request()` allocates `struct cpt_info_buffer`, builds gather/scatter lists through `setup_sgio_list()`, maps completion/result buffers, fills `struct cpt_vq_command` and `union cpt_inst_s`, reserves a pending entry, posts through `send_cpt_command()`, and returns asynchronously. `process_pending_queue()` scans pending entries, checks completion codes and timeout windows, cleans DMA resources, and calls request callbacks. `cptvf_do_request()` verifies device readiness and SE/AE type compatibility before submission.

State and persistence: state is coherent command ring contents, pending queue entries, mapped input/output buffers, completion DMA memory, and per-request timeout metadata. Hardware advances doorbells and writes completion structures.

Dependencies and integration points: depends on VF queue setup in `cptvf_main.c`, crypto request structures in `cptvf_algs.h`, CPT instruction/result layouts, Linux DMA mapping, jiffies, and callbacks into the crypto API.

Risks and test signals: risks include a cleanup bug unmapping `list[i]` instead of `list[j]` after partial DMA-map failure, callbacks called after `pentry` fields are cleared, possible busy queue deadlocks under lock nesting, direct DMA mapping of virtual buffers, and timeout handling that may free resources while hardware later writes completion. Test signals include multi-buffer SG map/unmap balance, pending threshold draining, fault/SWERR completion cleanup, request timeout tests, and crypto self-tests under queue pressure.
