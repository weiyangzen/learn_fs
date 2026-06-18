# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isp_param/interface/ia_css_isp_param.h

Purpose: declares memory descriptor helpers and lifecycle functions for ISP parameter blocks.

Important APIs: setters/getters for host/CSS/ISP segment descriptors, `ia_css_init_memory_interface`, `ia_css_isp_param_allocate_isp_parameters`, `destroy_isp_parameters`, `load_fw_params`, `copy_isp_mem_if_to_ddr`, and `enable_pipeline`.

Control flow/state: callers describe per-parameter-class/per-memory sizes and offsets, allocate host and DDR parameter storage, optionally map firmware offset tables, copy host parameter images to DDR, then toggle the mandatory DMEM disable bit to enable the pipeline.

Dependencies/integration: uses `ia_css_isp_param_types.h`, `ia_css_err.h`, HMM DDR memory, and pipeline binaries' memory-offset metadata.

Risks: pointer/size arrays are indexed by enums with minimal runtime validation. `enable_pipeline` assumes the first DMEM param word is a control/disable field by protocol.

Test signals: allocation with sparse and full memory initializers, cleanup after partial allocation failure, copy size mismatch returning `-EINVAL`, firmware-offset initialization, and pipeline enable bit clearing.
