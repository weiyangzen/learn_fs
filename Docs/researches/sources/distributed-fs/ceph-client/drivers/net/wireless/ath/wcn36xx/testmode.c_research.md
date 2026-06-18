# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/testmode.c

## Purpose
`testmode.c` implements the nl80211 testmode entry point for WCN36xx factory/production-test messages. It accepts a vendor test command, validates netlink attributes, handles a local build-release query, and forwards other PTT messages to firmware through the SMD HAL.

## Important APIs, Types, and Functions
- `wcn36xx_tm_policy` accepts `WCN36XX_TM_ATTR_CMD` as `NLA_U16` and `WCN36XX_TM_ATTR_DATA` as bounded binary data up to `WCN36XX_TM_DATA_MAX_LEN`.
- `struct build_release_number` is the packed response body for `MSG_GET_BUILD_RELEASE_NUMBER`.
- `wcn36xx_tm_cmd()` parses the netlink payload, requires command `WCN36XX_TM_CMD_PTT`, and dispatches to `wcn36xx_tm_cmd_ptt()`.
- `wcn36xx_tm_cmd_ptt()` interprets the incoming `struct ftm_rsp_msg`, either fills local firmware version fields or calls `wcn36xx_smd_process_ptt_msg()`, then replies with `cfg80211_testmode_reply()`.

## Control Flow
Netlink testmode data enters `wcn36xx_tm_cmd()`, is parsed by `nla_parse_deprecated()`, and must contain a command attribute. Unsupported commands return `-EOPNOTSUPP`. PTT data is inspected as an FTM message. The build-release message is answered directly from `wcn->fw_major/minor/version/revision`; all other payloads are sent to firmware, and if firmware returns no response the code echoes the request with the response status.

## State and Persistence Behavior
This file does not own persistent state. It reads firmware version fields from `struct wcn36xx`, temporarily allocates firmware response buffers, and relies on SMD to perform any firmware-side state change represented by PTT messages.

## Dependencies and Integration Points
It integrates nl80211 testmode (`cfg80211_testmode_alloc_reply_skb()`, `cfg80211_testmode_reply()`), netlink attribute parsing, `testmode.h`/`testmode_i.h` protocol definitions, and the SMD PTT function. It is compiled only when `CONFIG_NL80211_TESTMODE` enables the external entry point.

## Risks and Test Signals
Risks include trusting the binary test payload layout, response length mismatches, and using `msg_body_length` for both request forwarding and reply allocation. Test signals are correct rejection of missing/oversized attributes, successful build-release responses, PTT round trips with firmware, no leaks when firmware allocates a distinct response, and clean behavior when firmware returns no response.
