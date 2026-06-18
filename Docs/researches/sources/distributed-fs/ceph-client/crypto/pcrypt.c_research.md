# sources/distributed-fs/ceph-client/crypto/pcrypt.c

Purpose: implements the `pcrypt` template, a parallelization wrapper for AEAD algorithms using padata worker infrastructure.

Important APIs, types, and functions: global `pencrypt`, `pdecrypt`, and `pcrypt_kset` hold padata instances and sysfs state. `struct pcrypt_instance_ctx` stores the child spawn, padata shells, and tfm counter. `struct pcrypt_aead_ctx` stores the child AEAD and callback CPU. Request paths are `pcrypt_aead_encrypt()`, `pcrypt_aead_decrypt()`, `pcrypt_aead_enc()`, `pcrypt_aead_dec()`, `pcrypt_aead_done()`, and `pcrypt_aead_serial()`.

Control flow: module init creates `/sys/kernel/pcrypt`, allocates padata instances for encryption and decryption, then registers the template. Instance creation supports AEAD only, allocates padata shells, grabs the child, copies algorithm properties, marks the instance async, and raises priority by 100. Tfm init selects a callback CPU round-robin over online CPUs and spawns the child. Encrypt/decrypt builds a child request and submits padata parallel work; if padata is busy, it falls back to direct child execution.

State and persistence: padata instances and sysfs kobjects persist while the module is loaded. Each tfm keeps its child and chosen callback CPU. Each request keeps a `pcrypt_request`, child `aead_request`, and padata metadata until completion.

Dependencies and integration points: depends on padata, kobject/sysfs, CPU masks, and AEAD crypto templates. It integrates with algorithm names such as `pcrypt(gcm(aes))`.

Risks: CPU hotplug changes may affect callback CPU selection after tfm init. Async completion ordering must route through the serial callback exactly once. Fallback direct execution changes scheduling behavior. Resource cleanup must unwind padata shells and ksets on partial init failures.

Test signals: async AEAD testmgr coverage, padata busy fallback, CPU hotplug while tfms exist, sysfs object creation/removal, child setkey/authsize forwarding, and module init rollback failures.
