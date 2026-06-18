# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_stc.h

## Purpose
This header is the central register, bitfield, board-description, and private-state contract for Comedi drivers using National Instruments DAQ-STC, E-series, 611x/6143/67xx, and M-series hardware. It gives the NI MIO driver family symbolic names for register offsets, masks, helper encoders, board capabilities, and per-device software shadows.

## Important APIs, Types, And Data
The file defines hundreds of `NISTC_*`, `NI_E_*`, `NI611X_*`, `NI6143_*`, `NI67XX_*`, `CS5529_*`, and `NI_M_*` register offsets and bit macros. Key macro groups cover interrupt acknowledge/enable/status, AI/AO command and mode registers, counters, DIO, RTSI trigger direction/output, clock output, FIFO status, calibration, M-series PFI filtering/output selection, PLL control, CDIO FIFO/command/mode, and AI/AO configuration. `enum` blocks define AI gain table IDs, calibration DAC types, and board register-family flags. `struct ni_board_struct` describes static board capabilities. `struct ni_private` holds runtime shadows, locks, calibration data, DMA channels/rings, board-type flags, route tables, RTSI shared mux usage, and AO arming state.

## Control Flow
The header has no functions, but its macros control low-level execution in `ni_mio_common.c` and PCI/ISA NI drivers. Write paths compose bitfields with macros such as `NISTC_AI_MODE1_SI_SRC(x)`, `NI_M_PFI_OUT_SEL(_c, _s)`, and `NI_M_PLL_CTRL_*`; read paths decode status with masks such as `NISTC_AI_STATUS1_ERR` and `NI_M_PLL_STATUS_LOCKED`.

## State And Persistence
Persistent runtime state is in `struct ni_private`, not in the header itself. Important state includes software copies of write-only or shared registers (`clock_and_fout`, interrupt enables, RTSI output registers, PFI output select registers), lock-protected window and DMA register access, calibration DAC shadows, EEPROM buffer, FIFO buffers, MITE DMA state, `routing_tables`, `rtsi_shared_mux_usage`, `rtsi_shared_mux_reg`, and `rgout0_usage`. These fields are per-device kernel memory and reset when the device is detached.

## Dependencies And Integration Points
The header includes `ni_tio.h` and `ni_routes.h`, tying STC register definitions to generic counter/timer and routing infrastructure. `ni_mio_common.c` uses the register IDs to map windowed STC registers to bus addresses, initialize devices, service interrupts, program AI/AO commands, manage RTSI/PFI routing, and configure M-series PLL/CDIO features. Board-specific PCI/ISA drivers populate `struct ni_board_struct`.

## Risks
Many macros encode hardware bit layouts directly; wrong masks or shifts can silently program invalid hardware states. Several registers alias read/write meanings or vary by family, such as M-series mappings and E-series-only interrupt enable registers. `struct ni_private` contains many soft shadow registers that must be updated under the right locks to avoid lost bits. The RTSI shared mux comments document ambiguous hardware semantics, so route changes in this area require particular caution.

## Test Signals
Compile-time coverage comes from all NI MIO family drivers. Runtime/unit signals include interrupt acknowledge/status handling, AI/AO command tests, route tests in `ni_routes_test.c`, and hardware or simulation tests for RTSI/PFI routing. Static tests should verify macro encoders and masks round-trip for representative fields such as `NISTC_RTSI_TRIG_TO_SRC`, `NI_M_PFI_OUT_SEL_TO_SRC`, PLL divisors, and CDIO mode sample-source fields.
