# sources/distributed-fs/ceph-client/include/linux/fsi-occ.h

Purpose: declares the FSI OCC client interface for submitting requests to IBM On-Chip Controller devices and defines the known OCC response/status codes.

Important APIs and types: response constants include in-progress, success, invalid command/length/data, checksum error, internal error, bad state, and several critical exception classes. `OCC_MAX_RESP_WORDS` caps responses at 2048 words. `fsi_occ_submit()` sends an opaque request buffer to a device and returns an opaque response with an in/out response length.

Control flow: OCC client drivers prepare a request, call `fsi_occ_submit()`, and interpret the response status codes and payload. The function abstracts the lower FSI/SBEFIFO transport and device binding.

State and persistence: no persistent state is defined here. OCC state is device/firmware runtime state, while request/response buffers are caller-owned transient data.

Dependencies and integration points: depends only on `struct device` and integrates with FSI OCC driver code, hwmon/power-management clients, and SBEFIFO transport where present.

Risks and test signals: risks include response length overflow, endian/protocol mismatch in callers, command-in-progress polling errors, and misclassification of critical OCC states. Tests should cover all response codes, maximum-sized responses, short responses, transport failures, and concurrent submissions if the provider supports them.
