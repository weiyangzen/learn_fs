# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/Makefile

## Purpose
Adds DCN2.0 VMID and display writeback objects to the AMD display build.

## Important APIs, Types, And Functions
Defines `DCN20 = dcn20_vmid.o dcn20_dwb.o dcn20_dwb_scl.o`, expands it to `AMD_DAL_DCN20`, and appends it to `AMD_DISPLAY_FILES`.

## Control Flow
Build-only flow: object names are path-prefixed and included in the aggregate object list.

## State And Persistence
No runtime state. Make variables persist only during build evaluation.

## Dependencies And Integration Points
Connects DCN20 VMID/page-table setup, writeback controller, and writeback scaler code into the parent display build system.

## Risks
The writeback implementation depends on scaler helper symbols from `dcn20_dwb_scl.o`; removing either object causes link failures. Adding DCN20 source files without updating this list can silently omit functionality.

## Test Signals
Module build should compile these three objects and resolve `dcn20_vmid_setup`, `dcn20_dwbc_construct`, `dwb_program_horz_scalar`, and `dwb_program_vert_scalar`.
