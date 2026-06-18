# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.h

Purpose: declares the DCN314 register table and PSR-SU support predicate while reusing the DCN31 hardware interface.

Important APIs and control flow: exports `dmub_srv_dcn314_regs` as a `struct dmub_srv_dcn31_regs` instance and declares `dmub_dcn314_is_psrsu_supported()`. There is no inline logic; `dmub_srv.c` consumes these symbols during ASIC setup.

State and persistence behavior: the header introduces no state. It is a binding layer that lets DCN314 share all DCN31 callback implementations with a different register table and firmware capability gate.

Dependencies and integration points: includes `dmub_dcn31.h`, so all DMUB window/mailbox/GPINT types and function declarations remain aligned with DCN31. Integrated only through `dmub_srv_hw_setup()`.

Risks and test signals: risks are limited to declaration/definition mismatches and stale export use if DCN314 diverges from DCN31 behavior. Test signals are successful link of `dmub_srv.c` references and runtime PSR-SU query coverage on DCN314 platforms.
