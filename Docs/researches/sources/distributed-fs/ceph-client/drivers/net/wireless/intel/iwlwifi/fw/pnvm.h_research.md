<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/pnvm.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/pnvm.h

Purpose: public PNVM loading interface and PNVM firmware filename helper.

Important APIs/types: defines `MVM_UCODE_PNVM_TIMEOUT`, `MAX_PNVM_NAME`, declares `iwl_pnvm_load()`, and provides `iwl_pnvm_get_fs_name()` to format `<firmware-prefix>.pnvm`.

Control flow: callers pass transport, notification wait data, firmware image, and SKU id to `iwl_pnvm_load()`. Filename generation delegates prefix construction to `iwl_drv_get_fwname_pre()`.

State and persistence: the header itself is stateless. The implementation persists PNVM state in transport.

Dependencies/integration: includes driver, notification wait, and image headers. Used by dump logging for user-facing missing-PNVM messages and by firmware startup flows that load PNVM.

Risks/test signals: filename truncation and timeout constant changes affect user-visible recovery. Test firmware prefix variations, buffer size, and load timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/pnvm.h -->
