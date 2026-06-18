# sources/distributed-fs/ceph-client/scripts/kconfig/qconf.h

## Purpose
`qconf.h` declares the Qt classes and enums used by the graphical Kconfig frontend.

## Important APIs, Types, and Functions
Enums define tree columns (`promptColIdx`, `nameColIdx`, `dataColIdx`), list modes (`singleMode`, `menuMode`, `symbolMode`, `fullMode`, `listMode`), and option modes (`normalOpt`, `allOpt`, `promptOpt`). Classes declared are `ConfigSettings`, `ConfigList`, `ConfigItem`, `ConfigItemDelegate`, `ConfigInfoView`, `ConfigSearchWindow`, and `ConfigMainWindow`.

The header exposes Qt signals and slots for menu navigation, item selection, option-mode changes, help/debug display, search, view switching, config loading/saving, and settings persistence.

## Control Flow
The header itself has no runtime flow, but Qt's meta-object system uses `Q_OBJECT`, signals, and slots declared here to route UI events in `qconf.cc`.

## State and Persistence
Class members define persistent UI state: root menu pointers, mode flags, option-mode flags, selected menus, search results, splitter pointers, saved actions, and static icons/actions. `ConfigSettings` persists state through QSettings.

## Dependencies and Integration Points
It includes Qt Widgets classes and `expr.h` for Kconfig types. It is consumed by `qconf.cc` and by Qt's moc generation during build.

## Risks and Edge Cases
The class declarations hold raw `struct menu *` and `struct symbol **` pointers into global Kconfig state; lifetime must remain process-wide. `ConfigItem` stores linked items in `menu->data`, so any change to menu data ownership must update the destructor logic. Qt API compatibility depends on the Qt5/Qt6 flags produced by `qconf-cfg.sh`.

## Test Signals
Successful moc/Qt compilation and interactive `xconfig` use validate this interface. Settings persistence, search windows, help panes, and tree updates are the important behavioral surfaces.
