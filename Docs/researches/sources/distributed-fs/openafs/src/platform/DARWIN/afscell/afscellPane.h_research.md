# Research: sources/distributed-fs/openafs/src/platform/DARWIN/afscell/afscellPane.h

Purpose: declares an Installer.app plugin pane for configuring the local AFS cell and optional alias during installation.

Important APIs and state: `afscellPane` subclasses `InstallerPane` and has outlets for `ThisCell` and `CellAlias` text fields. The implementation overrides pane title, entry, and exit behavior.

Control flow and persistence: no methods are declared in the header beyond inherited installer lifecycle. The implementation reads current config and writes temporary installer handoff files.

Dependencies and integration: imports Cocoa and `InstallerPlugins/InstallerPlugins.h`. Built as `afscell.bundle` by the Darwin Makefile.

Risks: depends on Apple's legacy Installer plugin API. The header's untyped outlets provide no compile-time binding checks.

Test signals: bundle load in Installer, text field outlet wiring, pane title localization, and installer forward/back navigation.
