
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/gth.h

Purpose: register and bitfield definitions for the Intel TH GTH switch, TSCU, and CTS trigger sequencer.

Important APIs/types/functions: defines `enum intel_th_output_parm` symbolic output controls, GTH register offsets (`GTHOPT`, `SWDEST`, `SCR`, `SCR2`, `STAT`, scratchpads), TSCU control/status bits, CTS event/action/status/control offsets, and wait-loop depths.

Control flow: no executable flow; `gth.c` uses these constants to reset ports, route masters, control store-enable, wait for pipeline-empty, resync timestamping, and trigger MSC window switches.

State and persistence: describes volatile MMIO state only.

Dependencies and integration: included by `gth.c`; relies on common Linux bit macros and Intel TH offset macros from `intel_th.h`.

Risks: incorrect offsets or masks directly misprogram hardware. The CTS/TSCU area is included in the GTH resource by `core.c`, so offset changes must stay aligned with subdevice resource windows.

Test signals: compile coverage plus hardware smoke tests for sysfs output parameters, GTH reset, TSCU resync, and CTS switch triggering.
