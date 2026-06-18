# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pm.h

Purpose: declares generic AMD XDNA PM helper functions and provides `amdxdna_pm_resume_get_locked()`, a convenience helper for callers that already hold `dev_lock`.

Important APIs: suspend/resume device callbacks, runtime resume get, autosuspend put, PM init/fini, and the inline locked resume helper.

Control flow: ioctl and AIE2 PM code often need runtime-resumed hardware while generic device state is protected by `dev_lock`. The inline helper temporarily unlocks `dev_lock`, calls `amdxdna_pm_resume_get()`, then reacquires the mutex.

State and persistence: no state; manipulates PM core state via functions in `amdxdna_pm.c`.

Dependencies: AMD XDNA PCI driver definitions and Linux device/PM types.

Risks: callers must be certain dropping `dev_lock` during resume cannot invalidate local assumptions. It should not be used when intermediate state must remain atomic across resume.

Test signals: lockdep coverage, concurrent ioctl/resume operations, and failure paths where resume returns error after the lock is reacquired.
