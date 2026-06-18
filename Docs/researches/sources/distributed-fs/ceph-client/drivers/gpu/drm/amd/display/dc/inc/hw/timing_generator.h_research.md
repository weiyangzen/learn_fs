# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/timing_generator.h

## Purpose

`timing_generator.h` defines the generic timing generator interface used by DCE CRTC and DCN OTG/OPTC implementations. It validates/programs timings, drives CRTC enable/disable, blanking, interrupts, global swap lock, DRR, CRC, DSC, ODM, and timing/debug readback.

## Important APIs, Types, And Functions

Types include CRTC position, global-swap-lock parameters, DRR and long-vtotal settings, CRTC state, keepout/stereo flags, CRC selection and parameters, OTG output mux destinations, timing synchronization mode, OTG/OPTC register-state structures, and the `timing_generator` object. `timing_generator_funcs` is the main API and covers timing validation/programming, vertical interrupt setup, CRTC enable/disable and phantom CRTC handling, position/frame count/scanout, blank colors, VGA disable, global swap lock, reset triggers, DRR/vtotal controls, static screen control, test patterns, `arm_vert_intr`, global sync, OPTC clock, stereo, DWB source, OPTC source, CRC configure/read, manual trigger, hardware timing readback, VTG params, DSC config/status, ODM bypass/combine/source segments, h-timing division, GSL, output mux, vblank alignment, long vtotal, double-buffer pending waits, vupdate keepout, lock status, OTG/OPTC register readout, and PWA frame sync.

## Control Flow

Modeset code validates timing, programs it with vready/vstartup/vupdate/pstate offsets, enables the CRTC/OTG, connects output muxes, and configures optional DSC/ODM/DRR/GSL state. IRQ code can arm vertical interrupts through the vtable before enabling interrupt masks. Disable paths blank, wait for pending updates, disable/reset, and optionally handle phantom pipes.

## State And Persistence Behavior

Timing generator objects persist in the resource pool. Hardware state includes active timing registers, counters, locks, blank colors, DRR ranges, CRC enablement, DSC mode, ODM mapping, and interrupt windows. State readout structs provide debug snapshots for reconstruction after hardware init or failures.

## Dependencies And Integration Points

The header depends on DC BIOS, CRTC timing, hardware color, and DSC definitions. It integrates with OPP/OPTC, IRQ vblank/vline setup, resource pipe topology, VRR/DRR, CRC debug, DSC, ODM, and global sync across multiple displays.

## Risks And Test Signals

Risks include invalid timing acceptance, lock/unlock deadlocks, missed vblank/vupdate interrupts, ODM segment errors, DRR limit bugs, and CRC/DSC state leaks. Test signals include modesets across timing ranges, VRR/DRR tests, vblank interrupt delivery, CRC captures, ODM combine, DSC modes, suspend/resume, and register-state dumps after underflow.
