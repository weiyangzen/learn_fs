
# sources/distributed-fs/ceph-client/arch/x86/include/asm/delay.h

Purpose: x86 delay-loop selection declarations.

Important APIs and control flow: includes generic delay APIs and declares `use_tsc_delay()`, `use_tpause_delay()`, and `use_mwaitx_delay()` for selecting TSC, TPAUSE, or MWAITX-backed delay implementations during CPU init.

State, dependencies, and risks: state is global/per-CPU delay backend selection in implementation files. Dependencies include TSC reliability, waitpkg/mwaitx features, and early init ordering. Risks include selecting a delay source before feature calibration or using unavailable low-power instructions. Test signals are boot calibration logs, delay accuracy tests, and CPU feature combinations.
