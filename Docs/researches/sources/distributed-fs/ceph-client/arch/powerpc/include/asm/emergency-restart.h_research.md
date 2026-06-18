## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/emergency-restart.h

Purpose: delegates PowerPC emergency restart support to the generic implementation.

Important APIs/types/functions: includes `<asm-generic/emergency-restart.h>` and defines no local API.

Control flow: generic emergency restart paths are used directly.

State and persistence: no local state.

Dependencies and integration: integrates generic restart handling into PowerPC builds.

Risks and test signals: risk is minimal and centered on generic include compatibility. Test signals include build coverage and emergency restart/reboot path tests.
