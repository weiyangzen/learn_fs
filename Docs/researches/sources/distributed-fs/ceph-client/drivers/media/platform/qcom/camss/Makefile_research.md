# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/Makefile

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/Makefile

Purpose: Defines the object list for the Qualcomm CAMSS aggregate driver and binds it to `CONFIG_VIDEO_QCOM_CAMSS`.

Important APIs/types/functions: `qcom-camss-objs` includes core `camss.o`, CSID common and generation files, CSIPHY variants, ISPIF, VFE variants, VBIF, video node support, and format support. `obj-$(CONFIG_VIDEO_QCOM_CAMSS) += qcom-camss.o` produces the module or built-in object.

Control flow/state: No runtime state. Object inclusion is static for the aggregate driver, so all SoC variant implementations are linked when CAMSS is enabled.

Dependencies/integration: Tightly coupled to declarations in headers such as `camss-csid.h`, `camss-csiphy.h`, and VFE ops headers; missing objects cause unresolved ops symbols for supported SoCs.

Risks/test signals: The common risk is adding a new SoC ops file but forgetting the Makefile. Test with `CONFIG_VIDEO_QCOM_CAMSS=m`, allmodconfig, and link checks for all exported `*_ops_*` symbols.
