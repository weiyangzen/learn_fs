## sources/distributed-fs/ceph-client/lib/reed_solomon/Makefile

Purpose: kernel build fragment for the Reed-Solomon library and its optional test module.

Important behavior: `obj-$(CONFIG_REED_SOLOMON) += reed_solomon.o` builds the library when configured. `obj-$(CONFIG_REED_SOLOMON_TEST) += test_rslib.o` builds the self-test module independently behind its test config.

Control flow: there is no procedural build logic beyond Kbuild object selection.

State and persistence: no runtime state. Build outputs are controlled by Kbuild.

Dependencies/integration: consumed by the kernel build system under the `lib/reed_solomon` directory. The main object includes the generic encoder/decoder bodies conditionally based on encoder/decoder width configs in `reed_solomon.c`.

Risks/test signals: configuration omissions can build the library without a desired width-specific encode/decode wrapper. Enabling `CONFIG_REED_SOLOMON_TEST` provides a direct randomized correctness signal through `test_rslib.o`.
