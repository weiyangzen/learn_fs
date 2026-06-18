# sources/cloud-native/ostree/mkdocs.yml

Purpose: This MkDocs configuration defines the OSTree documentation site name and navigation tree. It maps top-level pages and manual chapters into a stable documentation structure.

Important keys: `site_name` is `OSTree`. The `pages` list includes Home, Contributing, Contributing Tutorial, and a Manual group with introduction, repository, deployments, atomic upgrades, adapting existing systems, formats, build systems/repos, repository management, and related projects.

Control flow and state: There is no runtime control flow. The file is declarative input to MkDocs; persistent output is the generated static documentation site. Navigation order in this file controls user-facing site layout.

Dependencies and integration points: Depends on MkDocs' legacy `pages` configuration shape and the referenced Markdown files. It complements the DocBook manpages by presenting guide-style documentation.

Risks: Modern MkDocs prefers `nav`; if the configured MkDocs version changes, this file may need migration. Any missing referenced Markdown file breaks or degrades docs builds. Navigation can drift from manpage coverage if new manuals are added but not listed here.

Test signals: Documentation CI should run `mkdocs build` and fail on missing files or config deprecations. Link-checking should verify the listed manual pages still exist and are reachable.
