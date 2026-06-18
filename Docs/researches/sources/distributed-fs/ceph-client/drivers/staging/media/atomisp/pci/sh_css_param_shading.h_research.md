# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_shading.h

Purpose: `sh_css_param_shading.h` declares the shading table generation/preparation helpers used by the CSS parameter writer. It separates shading-specific table work from the much larger parameter manager.

Important APIs/types/functions: `sh_css_params_shading_id_table_generate()` allocates an identity shading table of a requested width and height. `prepare_shading_table()` prepares an input shading table for a specific binary, sensor binning, and BDS factor and returns a target table.

Control flow and state: the header contains no state. The implementation allocates returned tables, and callers are responsible for freeing them with `ia_css_shading_table_free()` unless ownership is retained in stream parameter state.

Dependencies and integration: it includes `ia_css_types.h` and `ia_css_binary.h` for shading table and binary descriptors. `sh_css_params.c` calls these helpers when `IA_CSS_SC_ID` parameters need to be written to DDR.

Risks: ownership is not obvious from the prototypes: both functions write through `struct ia_css_shading_table **target_table`, and callers must handle NULL on allocation failure and cleanup existing temporary tables before overwriting pointers.

Test signals: compile tests should ensure the header remains lightweight. Integration tests should exercise parameter updates with no shading table, direct table use, and legacy conversion mode.
