<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/debug.c

Purpose: Provides a shared helper to render `enum nl80211_iftype` operation modes as readable strings for ath-family diagnostics.

Important APIs/types/functions: Exports `ath_opmode_to_string()`, mapping UNSPEC, ADHOC, STATION, AP, AP-VLAN, WDS, MONITOR, MESH, P2P client/GO, OCB, and default UNKNOWN.

Control flow: A single switch translates an interface type to a static string.

State and persistence: Stateless.

Dependencies and integration points: Includes `ath.h` and Linux export support; used by ath drivers for logging/debug output.

Risks and test signals: Risk is new nl80211 interface types falling to UNKNOWN until updated. Test signals are compile coverage and expected names in debug logs for each supported interface mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/debug.c -->
