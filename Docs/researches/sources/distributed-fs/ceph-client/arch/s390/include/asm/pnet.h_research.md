# sources/distributed-fs/ceph-client/arch/s390/include/asm/pnet.h

Purpose: This header declares lookup of IBM Z physical network identifiers by Linux device and port.

Important APIs/types/functions: `pnet_id_by_dev_port(struct device *dev, unsigned short port, u8 *pnetid)` is the single API.

Control flow: Network or device code passes a device and port number; implementation fills the PNET ID associated with platform topology metadata.

State and persistence: State lives in firmware/device attributes queried by the implementation, not in the header.

Dependencies and integration points: It depends on Linux device model types and integrates network, PCI/CCW devices, and platform PNET ID discovery.

Risks and test signals: Incorrect port mapping can bind networking policy to the wrong physical network. Tests should cover devices with/without PNET IDs, multi-port adapters, error returns, and hotplug.
