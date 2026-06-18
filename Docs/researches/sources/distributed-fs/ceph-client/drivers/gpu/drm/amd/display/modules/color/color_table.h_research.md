# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/color/color_table.h

Purpose: Declares dimensions and accessors for module-global PQ/de-PQ lookup tables used by AMD DC color curve generation.

Important APIs and types: Constants `NUM_PTS_IN_REGION` (16), `NUM_REGIONS` (32), and `MAX_HW_POINTS` (512) define the hardware point grid. `enum table_type` selects PQ or de-PQ. Functions expose init-state check, table pointer retrieval, and init-state mutation.

Control flow: `color_gamma.c` uses the dimensions to build the X distribution and calls the accessors before/after precomputing tables. The extra `+2` allocation is in the C file, while this header defines the logical maximum.

State and persistence: No state here; state is in `color_table.c`.

Dependencies and integration points: Includes `dc_types.h` for `struct fixed31_32` availability through DC type includes. Integrated tightly with `color_gamma.c` and any future color table consumers.

Risks: Changing point counts requires updating hardcoded PQ numerator table and curve algorithms. Invalid `table_type` handling returns NULL/false in implementation. Consumers must honor `MAX_HW_POINTS` inclusive loops used by gamma code.

Test signals: Compile-time dimension checks, curve generation with all 513 logical points, and table initialization state transitions.
