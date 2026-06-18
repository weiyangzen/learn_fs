# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/kexec.c

## Purpose
Handles pSeries CPU teardown during kexec and crash shutdown. It unregisters hypervisor per-CPU facilities when safe and tears down the active interrupt controller backend.

## Important APIs, Types, And Functions
The file defines `pseries_kexec_cpu_down(int crash_shutdown, int secondary)`. It uses `firmware_has_feature(FW_FEATURE_SPLPAR)`, `unregister_dtl`, `unregister_slb_shadow`, `unregister_vpa`, `xive_enabled`, `xive_teardown_cpu`, `xive_shutdown`, and `xics_kexec_teardown_cpu`.

## Control Flow
For shared-processor LPARs on non-crash kexec, the current CPU unregisters its dispatch trace log if enabled, then unregisters SLB shadow and VPA areas using the hardware CPU id. It logs but does not abort on deregistration failure. Interrupt teardown then branches on XIVE versus XICS: XIVE per-CPU teardown always runs and the primary CPU shuts down XIVE globally; XICS uses its kexec CPU teardown with the secondary flag.

## State And Persistence
The function clears hypervisor registrations for DTL, SLB shadow, and VPA so the next kernel is less likely to inherit stale host references. It does not persist state in the filesystem and deliberately avoids unregister hcalls during crash shutdown.

## Dependencies And Integration Points
Integrates with the architecture kexec path, SPLPAR per-CPU registration code in `lpar.c`, XIVE/XICS interrupt controllers, paca/lppaca state, and PAPR hcall wrappers.

## Risks And Edge Cases
Crash shutdown skips unregistering hypervisor facilities, trading cleanup for lower risk while the kernel may be corrupted. Failed unregisters are warnings only. The primary/secondary distinction matters for avoiding duplicate global XIVE shutdown. Incorrect CPU ids would leave hypervisor references to old memory.

## Test Signals
Exercise normal kexec and crash kexec on SPLPAR and non-SPLPAR systems, with both XIVE and XICS configurations. Check logs for deregistration warnings and validate that the next kernel boots without stale VPA/DTL or interrupt-controller state.
