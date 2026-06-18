<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/cldma.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/cldma.h

Purpose: public interface for the AVS CLDMA code-loader helper.

Important APIs, types, and functions: declares opaque `struct hda_cldma`, external singleton `code_loader`, default buffer size `AVS_CL_DEFAULT_BUFFER_SIZE`, and all lifecycle/control functions implemented in `cldma.c`.

Control flow: callers initialize the singleton, set transfer data, call setup/start/transfer as needed, feed interrupts into `hda_cldma_interrupt()`, then stop/reset/free during error handling and teardown.

State and persistence: hides the CLDMA object internals, so state is owned by `cldma.c`. The singleton declaration makes the loader globally shared within the AVS module.

Dependencies and integration points: included by `core.c` for free/init and by `loader.c` for firmware transfer. Requires HDA bus types via function signatures but avoids exposing register details.

Risks: opaque singleton API does not enforce serialization at compile time. Call order matters: data/setup/interrupt handling must be coordinated by loader/core code.

Test signals: compile-time users include only the header, and runtime firmware loading succeeds on CLDMA-attributed platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/cldma.h -->
