# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/Kconfig

## Purpose
This Kconfig file introduces the Chips&Media media platform driver menu and includes subordinate codec driver Kconfig files.

## Important APIs, Types, and Functions
It contains a comment and sources `drivers/media/platform/chips-media/coda/Kconfig` and `drivers/media/platform/chips-media/wave5/Kconfig`.

## Control Flow
When the parent media platform Kconfig reaches this file, it delegates option definitions to the Coda and Wave5 subdirectories.

## State and Persistence
No runtime state exists. The persisted effect is the user's kernel `.config` selections from the sourced child files.

## Dependencies and Integration Points
It integrates Chips&Media codec IP options into the larger media platform Kconfig hierarchy.

## Risks and Edge Cases
Incorrect `source` paths hide entire driver families. Adding symbols here instead of child files could make ownership and menu organization less clear.

## Test Signals
Run Kconfig menu traversal and allmodconfig to confirm both Coda and Wave5 options are visible and parse without warnings.
