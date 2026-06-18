# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h

## Purpose
This header defines DCN 1.0 display interrupt source IDs and context IDs for AMDGPU's interrupt handler and display IRQ services. It maps a broad set of DCN display events to the numeric `src_id`/`context_id` values emitted through the SOC15 IH path.

## Important APIs, Types, And Data
The file is constants-only and contains `DCN_1_0__SRCID__*` and matching `DCN_1_0__CTXID__*` macros. Groups include DC I2C software/hardware completion and DDC read requests, DCCG/DMU/DIO/WB/DPP/HUBP/HUBBUB/MPC/OPP/OPTC/MMHUBBUB/AZ performance counters, RBBMIF and DMCU internal events, ABM histogram/luma/backlight events, DPCS TX/RX errors, HPD and HPD RX events, audio endpoint format/enable/disable events, AUX software/LS/GTC events, DIG stream-disable and fast-training events, MCIF writeback and scaler conflicts, DCPG power up/down events, OTG timing/snapshot/trigger/vertical/ext-sync/DRR events, vblank/vline and HUBP VM context errors, MPCC stalls, vstartup/vready/vsync, HUBP flip/flip-away, no-lock vupdate events, and DMCUB outbox readiness.

Repeated source IDs use context IDs to distinguish channels or subevents. For example HPD and HPD RX share source 9 with context IDs, OTG snapshot/control groups use per-OTG source IDs with context selectors, and DMCUB outbox high/low priority uses source `0x68` with distinct contexts.

## Control Flow
There are no functions. Display code registers these IDs with `amdgpu_irq_add_id()` and DC IRQ service code maps incoming `amdgpu_iv_entry` records to display IRQ sources. Several paths register contiguous ranges using the first macro plus the number of CRTCs or OTGs.

## State And Persistence
The constants are immutable. Runtime state is the interrupt registration tables, enabled IRQ masks, and DC interrupt-source mapping built from these numbers. Correct mappings persist for the device lifetime and across mode-set operations.

## Dependencies And Integration Points
The header is included by `amdgpu_dm.c` and many DC IRQ service implementations from DCN 1.0 through newer DCN generations that reuse these source IDs. It integrates with SOC15 IH client `DCE`, HPD/AUX handling, page-flip/vblank delivery, timing events, DMUB message processing, and display error diagnostics.

## Risks
Many source IDs are overloaded by context ID; registering or decoding only the source can deliver the wrong event. Range assumptions depend on contiguous hardware numbering for OTGs, HUBPs, and CRTC-related events. The table contains historical naming mismatches and comments for later DCN users, so renaming macros can break broad display IRQ code even if values stay the same.

## Test Signals
Compile all DC IRQ service variants. Runtime validation should cover HPD plug/unplug and HPD RX, AUX/I2C transactions, vblank/page-flip interrupts, vstartup/vready/vupdate events, DMCUB outbox interrupts, display power-domain changes, link training, underflow/error reporting, and multi-CRTC systems where range-based registration is used.
