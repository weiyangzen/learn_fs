# sources/distributed-fs/ceph-client/security/integrity/ima/ima_queue.c

Purpose: Maintains the append-only IMA measurement list, duplicate-detection hash table, PCR extension path, kexec serialization sizing, reboot suspension, and violation digest initialization.

Important APIs/types/functions: Exports `ima_measurements`, `ima_htable`, `ima_add_template_entry()`, `ima_restore_measurement_entry()`, `ima_get_binary_runtime_size()`, `ima_init_reboot_notifier()`, and `ima_init_digests()`. Internals include `ima_lookup_digest_entry()`, `ima_add_digest_entry()`, `ima_pcr_extend()`, and the reboot notifier.

Control flow: `ima_add_template_entry()` locks `ima_extend_list_mutex`, refuses additions after measurements are suspended, checks the hash table for existing non-violation digests unless disabled, links a queue entry to `ima_measurements`, optionally indexes it by digest, extends the selected TPM PCR, and audits the result. Violations use a preallocated all-0xff digest bank array to invalidate PCRs. Kexec restore uses `ima_restore_measurement_entry()` to relink entries without PCR extension.

State and persistence: Measurements are never removed during a boot cycle. `binary_runtime_size` tracks serialized list size for kexec handoff. `ima_measurements_suspended` prevents late logging once reboot/kexec has started. The hash table stores digest/PCR pairs for duplicate suppression.

Dependencies and integration: Depends on TPM PCR APIs, IMA template entries, audit helpers, RCU list traversal, and reboot notifiers. It is consumed by measurement display, kexec restore/save code, and all IMA measurement producers.

Risks and test signals: Watch for hash-table duplicate false positives across PCRs, memory accounting overflow, lock ordering around TPM calls, reboot-time races, and correct audit causes for `hash_exists`, suspended measurements, ENOMEM, and TPM errors. Tests should exercise duplicate measurement suppression, violation extension, TPM absent behavior, and kexec restore sizing.
