# sources/distributed-fs/ceph-client/include/linux/ndctl.h

Purpose: kernel wrapper around the NVDIMM control UAPI that defines common in-kernel constants.

Important APIs and types: includes `uapi/linux/ndctl.h` and defines `ND_MIN_NAMESPACE_SIZE` as `PAGE_SIZE`.

Control flow: NVDIMM/libnvdimm code includes this header to access ndctl UAPI definitions and the minimum namespace-size constraint during namespace creation or validation.

State and persistence: no state is owned here. The size constant affects validation of persistent namespace configuration.

Dependencies and integration points: depends on ndctl UAPI and `PAGE_SIZE` availability through kernel includes. It bridges ioctl/control-plane definitions into kernel NVDIMM code.

Risks and test signals: risks include accepting namespaces smaller than a page if callers bypass the constant, or architecture page-size changes affecting namespace minimums. Test namespace create/resize validation around `PAGE_SIZE` and compile users of ndctl UAPI definitions.
