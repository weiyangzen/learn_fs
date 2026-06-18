<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/intro_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/intro_page.cpp

Purpose: Implements the wizard introduction page.

Important APIs/functions: `IntroPageDlgProc` delegates common handling, initializes buttons, and moves to the first information page on Next. `OnInitDialog` enables only the Next button.

Control flow: This is a simple entry page with no validation or data capture.

State and persistence: No `g_CfgData` mutations and no durable writes.

Dependencies and integration points: Uses `WizStep_Common_DlgProc`, `g_pWiz`, and resource/template wiring.

Risks: Minimal. It relies on common wizard handling for cancel/help/graphic setup.

Test signals: Verify initial wizard state, Next navigation to `sidSTEP_TWO`, cancel behavior, and help routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/intro_page.cpp -->
