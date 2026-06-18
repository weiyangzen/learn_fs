<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongarch-cpu.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongarch-cpu.c

## Purpose
Implements the root LoongArch CPU interrupt controller and ACPI/OF cascade discovery for LIOINTC, EIOINTC, AVECINTC, LPC, PCH PIC, and PCH MSI domains.

## Important APIs, Types, And Functions
Global `irq_domain` is the CPUINTC domain and `cpuintc_handle` is its fwnode. `cpu_irq_controller` masks and unmasks CPU interrupt bits in CSR ECFG. Important functions are `handle_cpu_irq()`, `loongarch_cpu_intc_map()`, `cpuintc_of_init()`, `cpuintc_acpi_init()`, `lpic_get_gsi_domain_id()`, `lpic_gsi_to_irq()`, and `acpi_cascade_irqdomain_init()`.

## Control Flow
OF init creates a linear domain over `EXCCODE_INT_NUM`, installs `handle_cpu_irq`, and returns. ACPI init masks CPU interrupt bits, creates a named fwnode domain, installs the handler, configures ACPI LPIC GSI domain routing and fallback translation, then parses MADT LIO PIC and EIO PIC entries and optionally initializes AVEC. Runtime CPU dispatch reads CSR ESTAT interrupt pending bits and forwards each set bit to the CPU domain.

## State And Persistence
State is minimal: root domain and fwnode handle plus CSR enable bits controlled by mask/unmask callbacks. ACPI GSI routing relies on global handles maintained by downstream Loongson irqchip drivers. No PM callbacks are present here.

## Dependencies And Integration Points
It depends on LoongArch CSR helpers, setup globals, ACPI MADT parsing, OF compatible `loongson,cpu-interrupt-controller`, and downstream functions from `irq-loongson.h`. It is the parent domain for platform interrupt controllers and optional AVEC MSI routing.

## Risks
The GSI domain selection logic depends on global handles being initialized by other drivers. CPU interrupt hwirq masking directly updates CSR ECFG, so wrong hwirq values can mask CPU exception inputs. ACPI init is idempotent only through the `irq_domain` guard.

## Test Signals
Test OF and ACPI boot, CPU timer/IPI interrupt delivery, ECFG mask/unmask, MADT LIO/EIO parsing, ACPI GSI translation to LPC/PCH/PIC domains, AVEC initialization when supported, and fallback GSI registration for PCH IRQ ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongarch-cpu.c -->
