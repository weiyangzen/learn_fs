# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs_fcpim.c

## Purpose
`bfa_fcs_fcpim.c` implements the FCS-layer FCP initiator nexus state machine. It negotiates FC-4 initiator-to-target readiness over an FCS remote port by sending PRLI, parsing PRLI responses, detecting initiator-only remote ports, creating/onlining the HAL `bfa_itnim_s`, delivering BFAD online/offline notifications, posting AENs, and handling PRLO. It bridges discovery/login state in FCS to the lower IO-execution machinery in `bfa_fcpim.c`.

## Important APIs, Types, And Functions
The file centers on `struct bfa_fcs_itnim_s` from `bfa_fcs.h`. Public functions are `bfa_fcs_itnim_create()`, `bfa_fcs_itnim_delete()`, `bfa_fcs_itnim_brp_online()`, `bfa_fcs_itnim_rport_offline()`, `bfa_fcs_itnim_is_initiator()`, `bfa_fcs_itnim_get_online_state()`, `bfa_fcs_itnim_lookup()`, `bfa_fcs_itnim_attr_get()`, `bfa_fcs_itnim_stats_get()`, `bfa_fcs_itnim_stats_clear()`, and `bfa_fcs_fcpim_uf_recv()`. HAL callbacks implemented here are `bfa_cb_itnim_online()`, `bfa_cb_itnim_offline()`, `bfa_cb_itnim_tov_begin()`, `bfa_cb_itnim_tov()`, and `bfa_cb_itnim_sler()`.

## Control Flow
Creation calls BFAD allocation, initializes the ITNIM to offline, and waits for rport progress. On FCS online, the state machine sends PRLI using an FCXP; FCXP allocation can wait asynchronously. A sent PRLI moves to the PRLI response state. Accept responses are parsed with `fc_prli_rsp_parse()`. If the remote port advertises initiator behavior, the ITNIM becomes a no-op initiator state and no HAL ITN is created. Otherwise the response records sequence recovery, REC support, task retry ID, and confirmation-completion support, then signals the rport that FC-4 FCS online is done.

After the rport/HAL rport is online, `bfa_fcs_itnim_brp_online()` drives the HAL-online event. The state creates a HAL ITN through `bfa_itnim_create()` if needed and calls `bfa_itnim_online()`. HAL completion calls back to `bfa_cb_itnim_online()`, which moves to online, notifies BFAD, logs, and posts an ITNIM online AEN. Offline from the rport notifies BFAD, calls `bfa_itnim_offline()`, logs disconnect/offline distinction based on lport state, and waits for HAL offline callback before acknowledging FC-4 offline to the rport.

PRLI errors enter a retry state with `BFA_FCS_RETRY_TIMEOUT` and up to `BFA_FCS_RPORT_MAX_RETRIES`; exhaustion causes implicit LOGO. PRLI command-not-supported moves offline without creating an ITN. Delete events cancel waits/discard FCXPs/stop timers as appropriate and free the BFAD ITNIM; if a HAL ITN exists, it is deleted first. PRLO unsolicited frames are routed to `bfa_fcs_rport_prlo()`.

## State And Persistence Behavior
State is runtime-only and encoded in the ITNIM state-machine function pointer plus fields in `bfa_fcs_itnim_s`: PRLI retry count, negotiated sequence-recovery/REC/FCP_CONF/task-retry flags, active FCXP, wait element, stats, BFAD handle, rport pointer, and optional HAL ITN pointer. The timeout callback increments stats and drives retry. AEN sequence uses the parent FCS `fcs_aen_seq`, but no persistent configuration is written here.

## Dependencies And Integration Points
The file depends on FCS rport/lport/fabric structures, FCXP allocation/send/discard, FC ELS PRLI builders/parsers, BFAD ITNIM allocation and online/offline/free callbacks, HAL FCPIM ITN APIs, and vendor event posting. It integrates with rport state via events such as `RPSM_EVENT_FC4_FCS_ONLINE`, `RPSM_EVENT_FC4_OFFLINE`, `RPSM_EVENT_LOGO_IMP`, and `RPSM_EVENT_DELETE`. It also updates driver-visible ITN timeout state in `bfa_cb_itnim_tov()`.

## Risks And Edge Cases
The state machine has many asynchronous cancellation points: FCXP allocation wait, in-flight PRLI, retry timer, HAL online/offline callbacks, rport offline/delete, and initiator-role changes. PRLI parse errors increment stats but do not always immediately send a state event, so behavior depends on surrounding timeout/offline progress. Well-known addresses skip HAL-online and AEN posting. If HAL ITN creation fails, the code offlines and requests rport delete. Logging/AEN behavior distinguishes connectivity loss from intentional offline by checking local-port online state.

## Test Signals
Tests should cover PRLI accept as target, PRLI accept as initiator, malformed PRLI response, LS_RJT command-not-supported, retryable response errors through retry exhaustion, FCXP allocation wait cancellation, rport offline/delete during PRLI send and PRLI wait, HAL ITN create failure, online/offline callback ordering, path-timeout callback effects, SLER-driven implicit LOGO, stats get/clear, attribute negotiation fields, and PRLO UF routing. Observable signals include ITNIM state encoding, BFAD online/offline/free callbacks, rport events, AEN records, and PRLI stats counters.
