# sources/distributed-fs/ceph-client/security/integrity/ima/ima_template.c

Purpose: Defines supported IMA template descriptors and fields, handles boot-time template selection/custom formats, initializes template field arrays, and restores template metadata from kexec-carried measurement lists.

Important APIs/types/functions: Built-in templates include `ima`, `ima-ng`, `ima-sig`, `ima-ngv2`, `ima-sigv2`, `ima-buf`, `ima-modsig`, and `evm-sig`. Public helpers include `ima_template_has_modsig()`, `lookup_template_desc()`, `template_desc_init_fields()`, `ima_init_template_list()`, `ima_template_desc_current()`, `ima_template_desc_buf()`, `ima_init_template()`, and `ima_restore_measurement_list()`.

Control flow: `ima_template=` selects an existing descriptor after validating SHA1/MD5 constraints for legacy `ima`; `ima_template_fmt=` validates a custom field string and binds it to the placeholder descriptor. `ima_init_template()` initializes the current template and the buffer template. Kexec restore parses a serialized header, rejects incompatible versions and legacy `ima`, resolves or creates template descriptors, initializes fields, parses field data, recalculates digests when needed, and restores queue entries without extending PCRs.

State and persistence: Template descriptors are held in the RCU-protected `defined_templates` list. Field arrays are allocated once per descriptor and reused. Restored custom descriptors are dynamically allocated and appended to the descriptor list.

Dependencies and integration: Uses field initializers/show functions from `ima_template_lib.c`, measurement queue restore, TPM bank sizing, canonical endian mode, and boot parameter parsing.

Risks and test signals: Risks include template format validation holes, maximum field/name length checks, kexec buffer bounds enforcement, endian conversion mistakes, and memory leaks for partially restored entries. Tests should include custom format validation, modsig template detection, kexec restore with truncated buffers, unknown restored formats, and unsupported legacy template restore.
