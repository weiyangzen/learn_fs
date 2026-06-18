# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/request_manager.h

Purpose: declares the software request, scatter/gather component, completion-buffer, and command-word structures shared by CPT VF algorithm code and the request manager.

Important APIs and types: constants define completion-code size, pending threshold, maximum SG counts, SG header size, and buffer count. `union ctrl_info` carries group, DMA mode, and SE/AE request type. `union opcode_info`, `struct cptvf_request`, `buf_ptr`, and `cpt_request_info` describe caller-visible requests. `struct sglist_component`, `cpt_info_buffer`, `vq_cmd_word0`, `vq_cmd_word3`, and `cpt_vq_command` describe DMA tables and hardware EI words.

Control flow and state: no functions execute here except declarations for `vq_post_process()` and `process_request()`. The layout controls how `cptvf_reqmanager.c` builds DPTR/RPTR/CPTR data.

Dependencies and integration points: depends on `cpt_common.h`, CPT VF queue code, and crypto algorithm request assembly.

Risks and test signals: risks include endian-sensitive bitfields, hard-coded maximum SG counts lower than some scatterwalk outputs, and `volatile` completion pointers not replacing proper DMA synchronization. Test signals include SG component byte order, control-word group/type matching PF queue binding, max-SG rejection behavior, and completion buffer alignment.
