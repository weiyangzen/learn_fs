# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/sm.c

Purpose: endpoint MHI state-machine helpers. It validates and performs RESET->READY, READY/M3->M0, M0->M3, and any-state->SYS_ERR transitions, writes endpoint status registers, sends state/environment events, and suspends or resumes channels around low-power transitions.

Important APIs: `mhi_ep_check_mhi_state()`, `mhi_ep_set_mhi_state()`, `mhi_ep_set_m0_state()`, `mhi_ep_set_m3_state()`, and `mhi_ep_set_ready_state()`.

Control flow: validation allows SYS_ERR from any state, READY only from RESET, M0 from READY or M3, and M3 from M0. `mhi_ep_set_mhi_state()` writes MHISTATUS state bits and READY/SYSERR bits. M0 transition resumes suspended channels if coming from M3, sends state-change event, and sends AMSS EE event when coming from READY. M3 transition updates state, suspends running channels, and sends state-change event. READY transition first verifies host-visible MHISTATUS is RESET and not already READY.

State and persistence: updates `mhi_cntrl->mhi_state`, channel states through main helpers, and hardware MHISTATUS bits. State is runtime-only and reset clears it.

Dependencies and integration: depends on endpoint MMIO helpers, event senders in `main.c`, channel suspend/resume helpers, `state_lock`, and SYS_ERR handling.

Risks: M1/M2 are explicitly unsupported. Failed M0/M3 transitions trigger SYS_ERR handling. READY requires host status to be reset, so ordering with host reset completion matters. Test signals include allowed and forbidden transitions, READY bit setting, SYSERR bit setting, M0 from READY versus M3, M3 suspend behavior, M0 resume behavior, and event-send failure paths.
