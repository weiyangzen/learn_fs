# sources/distributed-fs/orangefs/src/io/flow/flowproto-dump-offsets/flowproto-dump-offsets.c

Purpose: diagnostic flow protocol intended to print offsets and sizes that would be transferred for different endpoint directions, rather than performing actual I/O.

Important APIs/functions: declares `flowproto_dump_offsets_ops`, initialize/finalize/getinfo/setinfo/post/find_serviceable/service, and four service helpers for MEM->BMI, BMI->MEM, BMI->TROVE, TROVE->BMI. Each service repeatedly calls the request processor with either `PINT_CLIENT` or `PINT_SERVER`, dumps segment offsets/sizes, totals bytes, and marks the flow complete or error.

Control flow/state: initialization checks BMI is initialized and clamps default buffer size to BMI max. `post()` stores the protocol id and marks state ready; service chooses a helper based on endpoints. Helpers loop until request done.

Dependencies/integration: depends on BMI info query, request processing, gossip logging, and old serviceable flow states. This file appears stale relative to the visible `flowproto_ops` and `flow_state`: it initializes more function pointers than the current struct declares, references `FLOW_SVC_READY`/`FLOW_ERROR`, and calls `PINT_Process_request` with capital `P` while the visible function is `PINT_process_request`.

Risks/test signals: currently likely disabled by its module file and may not compile without legacy compatibility macros. If revived, reconcile the ops signature, state enum, and function names first. Tests should validate pure offset dumping for all endpoint pairs, no side effects on BMI/Trove, request cursor advancement, and output for discontiguous memory/file requests.
