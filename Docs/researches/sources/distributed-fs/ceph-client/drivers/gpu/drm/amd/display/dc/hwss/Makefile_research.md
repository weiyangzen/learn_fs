# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/Makefile

Purpose: lists the hardware sequencer source objects included in AMD Display Core builds. It selects DCE generation files unconditionally or under SI support, and DCN generation files under floating-point Display Core support.

Important build logic: `CONFIG_DRM_AMD_DC_SI` gates `dce60_hwseq.o`. DCE80, shared DCE, DCE100, DCE110, DCE112, and DCE120 objects are added to `AMD_DISPLAY_FILES`. `CONFIG_DRM_AMD_DC_FP` gates DCN objects from DCN1.0 through DCN4.2, each adding both `*_hwseq.o` and `*_init.o` where present. Paths are formed with `$(addprefix $(AMDDALPATH)/dc/hwss/<generation>/,...)`.

Control flow: this is build-system flow only. Kbuild includes the selected object paths in the AMD display driver. The ordering groups legacy DCE first, then DCN generations, with newer entries including DCN35, DCN351, DCN401, and DCN42.

State and persistence: no runtime state. The file persists build membership: missing an object prevents the corresponding generation's hardware sequencer code from being linked, while stale entries break builds when files are renamed or config gates change.

Dependencies and integration points: depends on top-level AMDGPU Display Core Kbuild variables such as `AMDDALPATH`, `AMD_DISPLAY_FILES`, `CONFIG_DRM_AMD_DC_SI`, and `CONFIG_DRM_AMD_DC_FP`. It integrates all `dc/hwss/*` generation folders into the kernel module build.

Risks and test signals: wrong gating can either omit required ASIC support or include FP-dependent DCN code in unsupported builds. Object list drift is likely when adding new generations. Signals include allmodconfig/allyesconfig kernel builds, `CONFIG_DRM_AMD_DC_FP=n` builds, SI-specific builds, and link checks that generation constructors referenced by resource code are present.
