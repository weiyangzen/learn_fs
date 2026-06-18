<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/softirq.h -->
# sources/distributed-fs/ceph-client/include/linux/softirq.h

Purpose: This compatibility header simply includes `linux/interrupt.h`, making softirq-related declarations available through the traditional `linux/softirq.h` include path.

Important APIs/types/functions: It declares no symbols of its own in this tree; all exported content comes from `interrupt.h`.

Control flow: There is no local control flow.

State and persistence: There is no local state.

Dependencies/integration: Any user including this file is implicitly coupled to the interrupt/softirq APIs provided by `linux/interrupt.h`. It preserves source compatibility for existing kernel code.

Risks and test signals: Risks are limited to include-order and dependency churn if `interrupt.h` changes. Test signal is compile coverage for files including `linux/softirq.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/softirq.h -->
