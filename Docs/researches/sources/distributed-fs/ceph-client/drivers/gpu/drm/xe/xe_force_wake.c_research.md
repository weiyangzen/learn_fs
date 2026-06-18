<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake.c

## Purpose
`xe_force_wake.c` manages GT forcewake domains. It initializes domain register mappings, reference-counts wake requests, programs wake/sleep controls, waits for acknowledgments, tracks awake domains, and provides domain names for diagnostics.

## Important APIs, types, and functions
Initialization functions are `xe_force_wake_init_gt()` and `xe_force_wake_init_engines()`. Core operations are `xe_force_wake_get()` and `xe_force_wake_put()`. Helpers include domain initialization, MMIO control/wait paths, wake/sleep wrappers, and `xe_force_wake_domain_to_str()`.

## Control flow and integration points
GT initialization always creates a GT domain, selecting MTL ack registers for graphics version 12.70+. Engine initialization adds render, VDBOX, VEBOX, and GSC domains based on GT type and engine mask. Get asserts a single domain bit or all-domains request, increments refs under spinlock, sends wake for domains transitioning from zero, waits for ack, records awake domains, and rolls back failed acks. Put decrements refs, sends sleep for domains reaching zero, waits for ack, and clears awake bits. SR-IOV VFs skip MMIO programming and waits.

## State and persistence behavior
`struct xe_force_wake` persists per GT. It stores initialized and awake masks plus per-domain refcounts/register fields. References returned by get must be put exactly once; scope classes in the header automate this for common flows.

## Dependencies, risks, and test signals
Dependencies include GT registers, MMIO wait/write helpers, SR-IOV mode, GT logging, and forcewake type masks. Risks include refcount imbalance, wake ack timeouts, `0xffffffff` MMIO unreliability, misuse of `XE_FORCEWAKE_ALL`, and skipped VF behavior hiding register access bugs. Test signals include forcewake get/put nesting, timeout/error injection, render/media/GSC domain coverage, SR-IOV VF paths, runtime PM interactions, and lockdep/irq-safe usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake.c -->
