# sources/distributed-fs/ceph-client/include/crypto/pcrypt.h

Purpose: declares the per-request wrapper used by pcrypt to parallelize crypto requests through padata.

Important APIs, types, and flow: `struct pcrypt_request` embeds `struct padata_priv` and a flexible request-private context tail. Helpers return the private context after the wrapper, cast a pcrypt request to its padata object, and recover the wrapper from a padata callback.

State and persistence: state is per request and lasts only through padata scheduling and completion.

Dependencies and integration: depends on padata and crypto request users. It integrates with pcrypt template code that splits encryption/authentication work across CPUs.

Risks and test signals: risks include context-size under-allocation, padata callback casting mistakes, and CPU hotplug interactions. Signals include pcrypt crypto self-tests, parallel workload stress, CPU hotplug under active requests, and request completion ordering checks.
