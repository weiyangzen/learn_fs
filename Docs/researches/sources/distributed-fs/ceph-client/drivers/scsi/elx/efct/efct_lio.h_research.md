# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_lio.h

## Purpose
`efct_lio.h` defines EFCT's private target-core data structures and diagnostic state flags. It bridges `struct efct_io` to `struct se_cmd`, describes target device/session/nport/vport/TPG objects, and declares target driver init/exit.

## Important APIs, Types, and Functions
Logging macros `efct_lio_io_printf` and `efct_lio_tmfio_printf` print command identity. `efct_set_lio_io_state` ORs state bits into `io->tgt_io.state`. `struct efct_scsi_tgt` stores target-wide max SGE/SGL, initiator/IO counters, watermarks, LIO objects, vport list, lock, and WWNN. `struct efct_node` is EFCT's target session node containing a kref, EFC node pointer, target-core session, active IO list, FC IDs, VPI/RPI, and abort count. `struct efct_scsi_tgt_io` embeds `struct se_cmd` and tracks DMA direction, task attribute, LUN, TMF/abort state, SG mapping progress, error, response sent, and transfer count. The header also defines LIO nport, vport, TPG attributes, TPG, node ACL, and vport list entries.

## Control Flow
The structures are populated by `efct_lio.c`: configfs allocates nports/vports/TPGs; session setup allocates `efct_node`; command receive clears and fills `efct_scsi_tgt_io`; target-core callbacks mutate state bits and SG progress; release paths free commands and IOs.

## State and Persistence Behavior
All state is in-kernel and mostly configfs/session scoped. State bits are cumulative diagnostics rather than an exclusive finite-state machine. TPG attributes mirror configfs booleans. Active IO lists and krefs protect session command lifetime.

## Dependencies and Integration Points
The header includes `efct_scsi.h` and `<target/target_core_base.h>`, exposing Linux target-core types to EFCT IO structures. Any layout changes affect command allocation, `container_of` conversions, and fabric ops.

## Risks
The cumulative state bitmask can hide ordering bugs because old bits are never cleared. `struct efct_scsi_tgt_io` embeds `se_cmd`, so alignment and lifetime must stay compatible with target-core expectations. `efct_node` lifetime depends on active IO krefs and target session teardown ordering.

## Test Signals
Build tests should cover `container_of` usage. Runtime tests should verify state bits through representative command paths, active IO list/kref balance, TPG attribute toggling, NPIV vport list management, and command release decrementing target IO counters.
