# sources/distributed-fs/ceph-client/samples/hid/hid_bpf_helpers.h

Purpose: declares HID-BPF kfuncs used by sample BPF programs.

Important APIs/functions: extern `__ksym` declarations for `hid_bpf_get_data`, `hid_bpf_attach_prog`, `hid_bpf_allocate_context`, `hid_bpf_release_context`, and `hid_bpf_hw_request`.

Control flow: header-only; BPF verifier/libbpf resolves kfunc symbols at load time.

State and persistence: none.

Dependencies and integration: included by `.bpf.c` files after `vmlinux.h` and BPF helper headers.

Risks: declarations must match kernel kfunc signatures exactly or BPF load will fail.

Test signals: BPF programs using this header should compile and load on kernels with HID-BPF kfunc support.
