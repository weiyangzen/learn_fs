# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/kernel/install.conf.d/37composefs.conf

Purpose: selects BLS layout for kernel-install in the BLS example.

Important APIs/types/functions: `layout = bls`.

Control flow: kernel-install reads this and emits Boot Loader Specification entries instead of UKIs.

State/persistence: persists kernel installation policy in the image.

Dependencies/integration: integrates with `kernel-install add-all` from the BLS Containerfile.

Risks/test signals: wrong layout would produce unbootable or wrong artifact type. Validated by example image boot.
