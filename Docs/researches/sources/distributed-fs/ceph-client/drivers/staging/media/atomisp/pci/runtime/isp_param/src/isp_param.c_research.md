# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isp_param/src/isp_param.c

Purpose: implements allocation, descriptor management, firmware-offset mapping, DDR copy, and pipeline-enable mutation for ISP parameters.

Important functions: descriptor setters/getters, `ia_css_init_memory_interface`, `ia_css_isp_param_allocate_isp_parameters`, `ia_css_isp_param_destroy_isp_parameters`, `ia_css_isp_param_load_fw_params`, `ia_css_isp_param_copy_isp_mem_if_to_ddr`, and `ia_css_isp_param_enable_pipeline`.

Control flow: allocation initializes every class/memory slot from optional ISP initializers, allocates zeroed host memory for any nonzero size, and allocates HMM DDR memory for non-`PARAM` classes. Cleanup frees both host and DDR addresses. Copy validates host and DDR sizes per memory, skips empty slots, and `hmm_store`s host bytes to DDR.

State/persistence: host pointers and HMM addresses persist in caller-owned segment structs until destroy. Firmware parameter offset pointers can either be null or point into a loaded firmware blob.

Dependencies/integration: HMM memory manager, kernel allocation, pipeline/binary parameter metadata, and ISP memory enum constants.

Risks: no bounds validation for enum indices. `ia_css_isp_param_enable_pipeline` writes through a char buffer cast to `uint32_t *` and assumes alignment/protocol. Partial allocation cleanup must be preserved to avoid HMM leaks.

Test signals: allocation failure injection, idempotent destroy, non-parameter class DDR allocation, copy mismatch error, and pipeline-enable mutation on empty and non-empty DMEM params.
