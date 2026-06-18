# sources/distributed-fs/ceph-client/include/uapi/linux/liveupdate.h

Purpose: defines the `/dev/liveupdate` userspace ioctl ABI for creating/retrieving named live-update sessions and preserving/restoring file descriptors across a kernel live update.

Important APIs and types: constants include `LIVEUPDATE_IOCTL_TYPE`, `LIVEUPDATE_SESSION_NAME_LENGTH`, device command IDs, and session command IDs. Device-level structs are `struct liveupdate_ioctl_create_session` and `struct liveupdate_ioctl_retrieve_session`. Session fd structs are `struct liveupdate_session_preserve_fd`, `struct liveupdate_session_retrieve_fd`, and `struct liveupdate_session_finish`. Ioctl macros include `LIVEUPDATE_IOCTL_CREATE_SESSION`, `LIVEUPDATE_IOCTL_RETRIEVE_SESSION`, `LIVEUPDATE_SESSION_PRESERVE_FD`, `LIVEUPDATE_SESSION_RETRIEVE_FD`, and `LIVEUPDATE_SESSION_FINISH`.

Control flow: userspace opens `/dev/liveupdate`, creates a named session, issues preserve-FD operations with opaque tokens, the kernel carries preserved resources through live update phases, then the new userspace/kernel side retrieves the session by name, retrieves each preserved fd by token, and finishes the session to release kernel ownership.

State and persistence: the ABI is explicitly stateful. Session names, tokens, preserved file references, and snapshot/restoration metadata survive the live update boundary in kernel-managed memory. Structs use a first-field `size` convention; future extension requires zeroed unknown tail bytes.

Dependencies and integration points: depends on `linux/ioctl.h` and `linux/types.h`. Integrates live update orchestration, fd-type-specific preservation support such as memfd/KVM/iommufd/VFIO, kernel reference counting, and userspace agents that coordinate update phases.

Risks and test signals: risks include nonzero unknown extension fields, token collision or lifetime bugs, restoring unsupported fd types, leaking preserved references on failed finish, and state-machine misuse outside the updated state. Test size negotiation, malformed names, duplicate sessions, preserve/retrieve token ordering, unsupported fd rejection, repeated finish, ENOENT paths, and live-update cycle cleanup.
