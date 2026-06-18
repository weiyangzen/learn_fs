# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/Makefile

Purpose: this Makefile declares the object files that make up the common AMD Display Core DCE hardware-programming layer and appends them to the global AMD display build list.

Important APIs and variables: `DCE` is the local object list and includes audio, stream encoder, link encoder, memory input, clock source, scaler filters, transform, output pixel processor, DMCU, ABM, input pixel processor, AUX, I2C hardware/software, DMUB PSR/ABM/replay/outbox/hardware-lock-manager, and panel control objects. `AMD_DAL_DCE = $(addprefix $(AMDDALPATH)/dc/dce/,$(DCE))` converts local object names into display-tree-relative paths. `AMD_DISPLAY_FILES += $(AMD_DAL_DCE)` appends them to the larger display driver build.

Control flow: Kbuild includes this fragment from the AMD display build. The object list controls which C files are compiled and linked into the AMDGPU display stack. It does not execute runtime logic.

State and persistence: there is no runtime state. Build state is the generated object list consumed by Kbuild.

Dependencies and integration: the file assumes `AMDDALPATH` and `AMD_DISPLAY_FILES` are defined by parent Makefiles. The included objects implement common DCE/DCN services used by display resource construction and hardware sequencing. `dce_abm.o` is the researched ABM implementation in this subset.

Risks: missing an object silently removes a hardware block implementation from the display build and may surface as link failures or disabled functionality. Adding an object without corresponding source or configuration support breaks Kbuild. The comment says register offsets/shifts/masks are stored in a `dec_hw`/`dce_hw` struct pattern, which matches the register-helper style used by these files.

Test signals: build AMD display with this Makefile included, verify every object in `DCE` has a source file, and check link coverage for DCE services such as ABM, DMCU, DMUB ABM, PSR, AUX, I2C, and panel control.
