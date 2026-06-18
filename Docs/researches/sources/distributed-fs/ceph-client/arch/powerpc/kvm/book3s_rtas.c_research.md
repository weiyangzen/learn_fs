# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_rtas.c

Purpose: this file implements in-kernel RTAS token definition and selected RTAS calls for Book3S KVM guests, currently focused on interrupt-controller operations such as XIVE/XICS set/get and interrupt masking.

Important APIs and types: `struct rtas_handler` maps RTAS names to handlers. `struct rtas_token_definition` stores per-VM token-to-handler bindings. `kvm_vm_ioctl_rtas_define_token()` lets userspace define or undefine supported RTAS tokens. `kvmppc_rtas_hcall()` executes a guest RTAS call. `kvmppc_rtas_tokens_free()` releases per-VM token definitions. Handler functions include `kvm_rtas_set_xive()`, `get_xive()`, `int_off()`, and `int_on()`.

Control flow: userspace defines a token by name; the code rejects duplicate token numbers and unsupported names under `rtas_token_lock`. At runtime, `kvmppc_rtas_hcall()` reads the guest `rtas_args` from guest physical memory in r4, validates argument array bounds, redirects `args.rets` into the copied args array, finds a matching token, calls its handler, restores the original return pointer, and writes the modified args back to guest memory.

State and persistence: token definitions persist on `kvm->arch.rtas_tokens` until undefinition or VM teardown. Handler results are written into guest RTAS return slots using big-endian RTAS format. No global mutable state is used.

Dependencies and integration: the interrupt RTAS handlers dispatch to XIVE if `xics_on_xive()` is true, otherwise XICS. The hcall path is invoked from PR PAPR handling when `H_RTAS` is requested and tokens exist. It uses KVM guest memory access under vCPU SRCU.

Risks: malformed guest RTAS pointers or excessive nargs fail out to userspace rather than returning an RTAS error because the return area cannot be trusted. Name matching uses fixed-size token argument names. Token definitions are only for known in-kernel handlers; userspace remains responsible for other RTAS services.

Test signals: define/undefine tokens, duplicate tokens, unsupported names, malformed guest args GPA, bad nargs/nret counts, set/get XIVE and int on/off on XICS and XIVE-backed systems, and VM teardown with live token lists.
