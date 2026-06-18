# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_hal.h

Purpose: declares the NITROX hardware-configuration and recovery helpers implemented by `nitrox_hal.c`.

Important APIs: exported declarations cover AQM rings/unit, EMU, packet input rings, packet solicit ports, NPS core/packet, POM, RNG, EFL, BMI, BMO, LBC, LBC invalidation, individual queue/port enable helpers, PF/VF mode programming, hardware info discovery, and PF-to-VF mailbox interrupt enable/disable.

Control flow and state: no state is stored here; it exposes functions that mutate persistent device CSRs and `ndev->hw`.

Dependencies and integration points: included by main device initialization, ISR recovery paths, mailbox/SR-IOV code, and any path needing to re-enable rings after errors.

Risks and test signals: risks include broad public surface making ordering requirements implicit and the misspelling of interrupt helper names elsewhere needing exact prototype matches. Test signals are clean compilation and callers invoking configuration after queue allocation and before request submission.
