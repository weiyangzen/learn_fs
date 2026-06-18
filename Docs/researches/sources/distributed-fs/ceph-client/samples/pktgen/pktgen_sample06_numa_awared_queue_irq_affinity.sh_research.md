# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample06_numa_awared_queue_irq_affinity.sh

## Purpose

This sample extends multiqueue pktgen setup with NUMA-aware CPU selection and IRQ affinity. It binds selected NIC queue IRQs to CPUs on the NIC's NUMA node and maps each pktgen device to a specific queue.

## Important APIs, Types, and Functions

Besides the common pktgen helper calls, it uses helper functions `get_iface_node`, `get_iface_irqs`, and `get_node_cpus`. It writes `/proc/irq/<irq>/smp_affinity_list`, configures `queue_map_min/max`, and sets `QUEUE_MAP_CPU`, UDP source-port randomization, and common packet attributes.

## Control Flow

The script discovers the interface NUMA node, IRQ list, and node CPU list, then rejects thread counts exceeding IRQ or CPU capacity. For each thread index it picks `cpu_array[i + F_THREAD]`, names the pktgen device `$DEV@$thread`, writes the corresponding IRQ affinity, adds the device to that pktgen thread, pins the pktgen queue number to `i`, applies packet fields, and runs pgctrl unless appending.

## State and Persistence Behavior

Unlike earlier samples, this script changes persistent host IRQ affinity in `/proc/irq`. Pktgen state is also persistent until reset. The script does not restore old IRQ masks on exit.

## Dependencies and Integration Points

It integrates directly with NIC queue IRQs, NUMA topology, and pktgen queue mapping. It requires root and helper support for sysfs/procfs topology discovery.

## Risks and Edge Cases

The IRQ affinity changes can affect unrelated traffic after the sample ends. Thread offset handling can index beyond `cpu_array` if helper bounds differ. Not all devices expose per-queue IRQs in the expected format.

## Test Signals

Check `/proc/irq/*/smp_affinity_list`, pktgen per-device results, `ethtool -S` queue counters, and NUMA-local CPU utilization.
