<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/xen-tpmfront.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/xen-tpmfront.c

Purpose: Xen frontend for a virtual TPM device. It exposes a Xen vTPM backend through the Linux TPM class by creating a shared page ring, grant reference, event channel, and `tpm_chip` whose class operations copy TPM commands/results through the Xen `vtpm_shared_page` protocol.

Important APIs/types/functions: `struct tpm_private` owns the Xenbus device, TPM chip, shared page, event channel, grant reference, IRQ, and read waitqueue. `wait_for_tpm_stat()` implements IRQ-backed or polling TPM status waits with freezer-aware signal handling. `vtpm_status()`, `vtpm_send()`, `vtpm_recv()`, and `vtpm_cancel()` are the `tpm_class_ops`. `setup_ring()` publishes `ring-ref`, `event-channel`, and `feature-protocol-v2` in Xenstore; `tpmfront_probe()`, `tpmfront_remove()`, `tpmfront_resume()`, and `backend_changed()` implement the Xenbus lifecycle.

Control flow: probe allocates private state, allocates a managed TPM chip, maps one shared page with a grant reference, allocates and binds an event channel IRQ, publishes the frontend ring details to Xenstore, moves to `Initialised`, gets TPM timeouts, and registers the chip. A TPM command waits for `VTPM_STATE_IDLE`, copies the request after the shared-page header and extra-page array, sets `length` and `VTPM_STATE_SUBMIT`, notifies the backend, waits for completion based on the TPM ordinal duration, and leaves result retrieval to `vtpm_recv()`. The IRQ handler wakes waiters only for `IDLE` and `FINISH` states. Backend state changes require protocol v2 before switching to `Connected`; close states unregister the device.

State and persistence: all state is runtime-only Xen frontend state. The shared page carries backend-visible `state`, `length`, and data; cancellation is represented by writing `VTPM_STATE_CANCEL` and notifying. Suspend/resume tears down and reprobes the frontend because in-flight vTPM commands are considered interrupted.

Dependencies and integration: depends on Xen PV device support, Xenbus, Xen grant tables, Xen event channels, TPM core helpers, and `xen/interface/io/tpmif.h`. It integrates with the generic TPM class rather than exposing its own character device.

Risks: shared-page offset and length validation is critical because data must fit in a single page after any `extra_pages` metadata. Timeout and signal paths collapse several failures to `-ETIME` and issue cancellation, so backend races around `CANCEL`, `IDLE`, and `FINISH` are subtle. `tpmfront_remove()` assumes TPM chip drvdata relationships are intact. Resume destroys the previous frontend, so missed unregister/free sequencing would leak event channels or grants.

Test signals: boot a Xen guest with a vTPM backend and verify `/dev/tpm*` registration, Xenstore `feature-protocol-v2`, event-channel interrupt completion, TPM selftests/known commands, timeout cancellation, backend disconnect, and suspend/resume or migration with an in-flight command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/xen-tpmfront.c -->
