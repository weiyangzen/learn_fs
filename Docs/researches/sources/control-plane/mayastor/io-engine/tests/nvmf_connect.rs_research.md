# sources/control-plane/mayastor/io-engine/tests/nvmf_connect.rs

Purpose: exercises concurrent nonblocking NVMf qpair connection creation and races between qpair connection attempts and device destruction.

Important APIs/types/functions: `MayastorTest`, `Lvs`, `LvsLvol`, `PoolArgs`, `Share`, `device_create`, `device_lookup`, `device_destroy`, `CoreError`, `BdevError`, `OnceCell`, `Pin`, `init_nvmf_share`, `spawn_get_io_handle_nonblock`, and `spawn_device_destroy`.

Control flow: `init_nvmf_share` creates an in-process LVS pool/lvol and shares it over NVMf. `nvmf_connect_async` repeats 20 times: imports the URI, launches three concurrent nonblocking I/O handle acquisitions, requires all succeed, and destroys the device. `nvmf_connect_async_drop` repeats with three handle acquisitions plus concurrent device destroy, expecting handle errors and destroy success. `deinit_nvmf_share` destroys the pool.

State and persistence behavior: no external persistence. State is shared lvol lifetime, imported NVMf device lifetime, and pending qpair connection futures.

Dependencies and integration points: in-process LVS, NVMf target share, SPDK qpair connection path, and device import/destroy APIs.

Risks: cfg branches in the drop test currently assert the same behavior in both cases; race behavior may change with SPDK connection implementation.

Test signals: three handles succeed without destroy, three handles fail when destroy races them, destroy succeeds in each loop, and pool cleanup succeeds.
