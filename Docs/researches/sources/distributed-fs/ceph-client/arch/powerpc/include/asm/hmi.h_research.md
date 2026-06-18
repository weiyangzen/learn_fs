# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hmi.h

Purpose: Declares Hypervisor Maintenance Interrupt event types and entry points for handling HMI conditions on PowerPC systems.

Important APIs, types, and functions: Defines event type constants for malformed event data, release, malfunction alert, processor recovery done, unknown events, and `struct pt_regs`-based handler declarations such as `hmi_exception_realmode` through interrupt macros elsewhere.

Control flow: Real-mode or early exception code receives an HMI, decodes event data, and dispatches to C handlers that can log, recover, or escalate.

State and persistence: No state is stored in the header. HMI state is in CPU/hypervisor event buffers and handler-side logs.

Dependencies and integration points: Integrates OPAL/pSeries HMI paths, machine-check style recovery, and low-level interrupt declarations.

Risks: HMI handling often runs with restricted context. Bad event decoding or unsafe calls from real mode can worsen platform failures.

Test signals: Injected HMI events for known and unknown types, malformed payload handling, real-mode entry coverage, recovery-done reporting, and builds across OPAL/pSeries configs.
