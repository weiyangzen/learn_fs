<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/Makefile

## Purpose

This Kbuild makefile builds the IBM virtual SCSI target/server module when `CONFIG_SCSI_IBMVSCSIS` is enabled. It combines the target fabric implementation and the local SRP helper into one module object.

## Important APIs and Build Rules

- `obj-$(CONFIG_SCSI_IBMVSCSIS) += ibmvscsis.o` selects the module or built-in object according to the kernel configuration.
- `ibmvscsis-y := libsrp.o ibmvscsi_tgt.o` links `libsrp.o` and `ibmvscsi_tgt.o` into the final `ibmvscsis` composite object.

## Control Flow, State, and Persistence

There is no runtime control flow or persistent state. The only behavior is build composition. Because `libsrp.c` is linked into `ibmvscsis`, its non-static symbols are available to `ibmvscsi_tgt.c` without creating a separate module dependency.

## Dependencies and Integration Points

The file integrates with Linux Kbuild and the kernel config symbol `CONFIG_SCSI_IBMVSCSIS`. It assumes `libsrp.c`, `libsrp.h`, `ibmvscsi_tgt.c`, and `ibmvscsi_tgt.h` are in the same directory.

## Risks and Edge Cases

- Any rename or split of `libsrp.o` or `ibmvscsi_tgt.o` must update this composition rule or the module will fail to link.
- Since `libsrp` is not built as a separately selectable object here, other users cannot depend on it through this makefile without refactoring.

## Test Signals

Build coverage is the key signal: enabling `CONFIG_SCSI_IBMVSCSIS=m` should produce `ibmvscsis.ko`; enabling it built-in should include both object files in vmlinux. Link errors around `srp_transfer_data`, `srp_target_alloc`, or target fabric callbacks indicate this rule or object ordering is broken.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/Makefile -->
