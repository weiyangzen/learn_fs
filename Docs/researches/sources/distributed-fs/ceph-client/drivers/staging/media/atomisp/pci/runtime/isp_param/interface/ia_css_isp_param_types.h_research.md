# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isp_param/interface/ia_css_isp_param_types.h

Purpose: defines the shared data model for ISP parameter memory classes and segment descriptors.

Important types/macros: `IA_CSS_ISP_DMEM`, `IA_CSS_ISP_VMEM`, `IA_CSS_NUM_ISP_MEMORIES`, `enum ia_css_param_class` (`PARAM`, `CONFIG`, `STATE`), `ia_css_isp_parameter`, host/CSS/ISP segment matrices, `ia_css_isp_param_memory_offsets`, and `union ia_css_all_memory_offsets`.

Control flow/state: no executable flow; these structs persist in binary/pipeline memory-parameter state and encode address/size pairs for each class and memory.

Dependencies/integration: uses public CSS types, platform alignment, and system memory enums. `isp_param.c`, debug parameter dumps, and binary loading consume these definitions.

Risks: class/memory dimensions must remain synchronized with firmware-generated offset structures. `union ia_css_all_memory_offsets` assumes aligned pointer slots and firmware layout compatibility.

Test signals: compile-time size/layout checks, iteration over `IA_CSS_NUM_PARAM_CLASSES` and `IA_CSS_NUM_MEMORIES`, and firmware offset parsing for all classes.
