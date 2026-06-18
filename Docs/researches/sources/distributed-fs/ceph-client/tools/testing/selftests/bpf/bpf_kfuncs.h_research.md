# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_kfuncs.h

Purpose: declares BPF kfunc prototypes used by selftests for dynptrs, sockaddr mutation, TCP reqsk assignment, casting, xattrs, fsverity, keys, and signature verification.

Important APIs and functions: dynptr constructors/slicers/adjusters, `bpf_sock_addr_set_sun_path`, `bpf_sk_assign_tcp_reqsk`, `bpf_cast_to_kern_ctx`, `bpf_rdonly_cast`, `bpf_get_file_xattr`, `bpf_get_fsverity_digest`, key lookup/put, PKCS#7 verification, and dentry xattr set/get/remove.

Control flow: header only; BPF verifier resolves weak/non-weak ksym references at load time.

State and persistence: kfuncs may return referenced objects or mutate kernel objects; callers own reference release obligations such as `bpf_key_put`.

Dependencies and integration points: assumes `vmlinux.h`/BPF context types are visible to includers and kernel exports matching these ksym names exist.

Risks: kernel-version and config sensitivity; incorrect dynptr buffer sizes or reference management can cause verifier errors; non-weak declarations require feature presence.

Test signals: selftests using this header validate kfunc availability, verifier type checking, and expected runtime return codes.
