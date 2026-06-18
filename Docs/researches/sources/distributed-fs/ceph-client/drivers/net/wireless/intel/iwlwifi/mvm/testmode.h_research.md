# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/testmode.h

## Purpose

`testmode.h` defines the nl80211 testmode attribute and command IDs understood by the MVM driver testmode implementation. It is a small shared contract rather than executable code.

## Important APIs and types

`enum iwl_mvm_testmode_attrs` defines nested testdata attributes: command selector, NoA duration, and beacon-filter state. `enum iwl_mvm_testmode_commands` defines `IWL_MVM_TM_CMD_SET_NOA` for GO NoA testing and `IWL_MVM_TM_CMD_SET_BEACON_FILTER` for toggling beacon filtering.

## Control flow, state, and dependencies

The file has no control flow or persistent state. It depends only on consumers using the enum values consistently when parsing `NL80211_ATTR_TESTDATA`. The command handlers elsewhere translate these enum values into driver or firmware operations.

## Risks

The risk is ABI drift: changing enum order or max values can break userspace test tools. Attribute validation must be strict in the consumer because this header does not encode type policy beyond comments.

## Test signals

Test signals are compile coverage and testmode parser tests that reject unknown attributes, require `IWL_MVM_TM_ATTR_CMD`, validate u32 payloads, and exercise NoA/beacon-filter command dispatch.
